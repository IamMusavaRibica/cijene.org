const map = new maplibregl.Map({
    container: 'map',
    style: 'https://tiles.openfreemap.org/styles/liberty',
    center: [15.9819, 45.8150],
    zoom: 9.3,
    maxBounds: [[13.36, 42.18], [19.69, 46.81]],
    // dragRotate: false,
    maxZoom: 16
});

map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right');





function setLocationCookie(lng, lat, radiusKm) {
    const cookieValue = [lng * 1e5, lat * 1e5, radiusKm * 1e3].map(Math.round).join(',');
    const maxAge = 400 * 24 * 60 * 60;  // 400 days, limited by some browsers
    document.cookie = `LocationPreference=${cookieValue}; Path=/; Max-Age=${maxAge}; SameSite=Lax`;
}

function readLocationCookie() {
    const m = document.cookie.match(/(?:^|;\s*)LocationPreference=(\d+),(\d+),(\d+)(?=;|$)/);
    const [lng, lat, radiusKm] = m ? [+m[1], +m[2], +m[3]] : [NaN, NaN, NaN];
    if ([lng, lat, radiusKm].every(Number.isSafeInteger)) {
        return { lng: lng / 1e5, lat: lat / 1e5, radiusKm: radiusKm / 1e3 };
    }
    return null;
}

function clearLocationCookie() {
    document.cookie = 'LocationPreference=; Path=/; Max-Age=0; SameSite=Lax';
}

(() => {
    const loc = readLocationCookie();
    const initialRadiusKm = loc ? loc.radiusKm : 1;
    if (loc) {
        map.setCenter([loc.lng, loc.lat]);
        map.setZoom(12.0);
    }
    LocationRadius.init(map, {
        startLngLat: loc && [loc.lng, loc.lat] || null,
        startRadiusKm: initialRadiusKm,
        controlPosition: 'top-left',
        controlOptions: {
            id: 'radius',
            labelText: 'Udaljenost u km',
            min: 0.2, max: 4, step: 0.2, value: initialRadiusKm,
            clearLabel: 'Ukloni odabir',
            onClear: () => {
                LocationRadius.removeMarker();
                clearLocationCookie();
            }
        },
        updateCallback: persist
    });

    function persist() {
        const marker = LocationRadius.getMarker();
        if (marker) {
            const { lng, lat } = marker.getLngLat();
            const radiusKm = LocationRadius.getRadiusKm();
            setLocationCookie(lng, lat, radiusKm);
        }
    }
})();



map.on('load', () => {
    map.addSource('store-locations', {type: 'geojson', data: {type: 'FeatureCollection', features: []}});
    map.addLayer({
        id: 'store-locations',
        type: 'symbol',
        source: 'store-locations',
    });

    fetch('/api/stores').then(r => r.json()).then(data => {
        const features = [];
        Object.entries(data).forEach(([storeId, storeMetadata]) => {
            const storeName = storeMetadata.name
            storeId.startsWith('_') || Object.entries(storeMetadata.locations).forEach(([locId, locData]) => {
                features.push({
                    type: 'Feature',
                    geometry: { type: 'Point', coordinates: [locData.lng, locData.lat] },
                    properties: { storeName, storeId, locId, city: locData.city, address: locData.address, googleMapsUrl: locData.google_maps_url }
                });
            });
        });
        map.getSource('store-locations').setData({ type: 'FeatureCollection', features });
        features.forEach(addMarker);
    });
});


function addMarker(feature) {
    const el = document.createElement('div');
    const { storeName, storeId, locId, city, address, googleMapsUrl } = feature.properties;
    el.className = 'store-marker';
    el.title = `${storeName} ${locId}`;  // tooltip on mouse hover
    el.style.backgroundImage = `url(/static/icons/${storeId}.png)`;
    el.style.backgroundSize = `contain`;
    el.style.width = `24px`;
    el.style.height = `24px`;

    /* ['click','mousedown','dblclick','contextmenu','touchstart'].forEach(type => {
        el.addEventListener(type, e => e.stopPropagation());
    }); */

    const popup = new maplibregl.Popup({ offset: 28, className: 'store-popup', focusAfterOpen: false });
    popup.setHTML(
        `<strong>${storeName}</strong><br>${address}<br>${city}`
            .concat(googleMapsUrl !== null ? `<br><a href="${googleMapsUrl}" target="_blank">Google Maps ></a>`: '')
    );
    // open google maps url in new tab on right click
    // el.addEventListener('contextmenu', e => {
    //     window.open(feature.properties.googleMapsUrl, '_blank');
    // })

    // add marker to map
    const marker = new maplibregl.Marker({element: el}).setLngLat(feature.geometry.coordinates).setPopup(popup).addTo(map);


    el.addEventListener('click', e => {
        marker.togglePopup();
        e.stopPropagation()
    });
}
