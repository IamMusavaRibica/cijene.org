window.LocationRadius = (() => {
    'use strict';

    let map = null;
    let marker = null;
    let control = null;
    let radiusKm = 1;
    let callback = () => {};
    let onMapClick = null;

    const ids = {
        source: 'lr-circle-src',
        fill: 'lr-circle-fill',
        line: 'lr-circle-outline'
    };

    // noinspection JSUnusedGlobalSymbols
    class RadiusControl {
        constructor({
            id = 'radius', labelText = 'Udaljenost u km',
            min = 1, max = 100, step = 5, value = 15,
            clearLabel = 'Ukloni odabir',
            onInput = null, onClear = null
        } = {}) {
            this.id = id;
            this.labelText = labelText;
            this.min = min; this.max = max; this.step = step; this.value = value;
            this.clearLabel = clearLabel;
            this.onInput = onInput;
            this.onClear = onClear;
        }

        onAdd(map) {
            this._map = map;

            const container = document.createElement('div');
            container.className = 'maplibregl-ctrl radius-ctrl';

            const rangeGroup = document.createElement('div');
            rangeGroup.className = 'maplibregl-ctrl-group radius-ctrl__group';
            container.appendChild(rangeGroup);

            // <label for="radius">Udaljenost u km</label><input id="radius" type="range" min="1" max="25" value="5" step="1" oninput="void 0;">

            const input = document.createElement('input');
            input.type = 'range';
            input.id = this.id;
            input.min = this.min;
            input.max = this.max;
            input.step = this.step;
            input.value = this.value;

            const label = document.createElement('label');
            label.setAttribute('for', this.id);
            label.textContent = this.labelText;

            ['mousedown', 'touchstart', 'wheel', 'dblclick'].forEach(evt =>
                rangeGroup.addEventListener(evt, e => e.stopPropagation(), {passive: true})
            );

            input.addEventListener('input', e => {
                const km = Number(e.target.value);
                this.onInput && this.onInput(km);
                callback();
            });

            rangeGroup.appendChild(label);
            rangeGroup.appendChild(input);



            const clearGroup = document.createElement('div');
            clearGroup.className = 'maplibregl-ctrl-group radius-ctrl__group radius-ctrl__group--clear';
            container.appendChild(clearGroup);

            const clearBtn = document.createElement('button');
            clearBtn.type = 'button';
            clearBtn.id = 'clear-marker-btn';
            clearBtn.className = 'radius-ctrl__clear';
            clearBtn.textContent = this.clearLabel;
            clearBtn.addEventListener('click', e => {
                e.preventDefault();
                e.stopPropagation();
                this.onClear && this.onClear();
            });
            clearGroup.appendChild(clearBtn);
            clearGroup.style.display = 'none';

            this._container = container;
            this._input = input;
            return container;
        }

        onRemove() {
            this._container.remove();
            this._map = undefined;
        }

        setValue(km) {
            this._input && (this._input.value = String(km));
        }
    }

    function setupCircleLayers() {
        if (map.getSource(ids.source))
            return;
        map.addSource(ids.source, { type: 'geojson', data: { type: 'FeatureCollection', features: [] }});

        map.addLayer({
            id: ids.fill,
            type: 'fill',
            source: ids.source,
            paint: {
                'fill-color': '#2563eb',
                'fill-opacity': 0.15
            }
        });

        map.addLayer({
            id: ids.line,
            type: 'line',
            source: ids.source,
            paint: {
                'line-color': '#2563eb',
                'line-width': 2
            }
        });
    }

    function updateCircle(lngLat = null, km = radiusKm) {
        const ll = lngLat ? maplibregl.LngLat.convert(lngLat) : (marker && marker.getLngLat());
        if (!ll)
            return;
        const circle = turf.circle([ll.lng, ll.lat], km, { steps: 128, units: 'kilometers' });
        const src = map.getSource(ids.source);
        src && src.setData(circle);
    }

    function setRadiusKm(km) {
        radiusKm = km;
        control && control.setValue(km);
        marker && updateCircle(marker.getLngLat(), km);
    }

    function attachMarkerEvents() {
        if (!marker) return;
        // drag event keeps circle in sync while dragging
        marker.on('drag', () => { updateCircle(marker.getLngLat(), radiusKm); });
        marker.on('dragend', () => { callback(); });
    }

    function createMarkerAt(lngLatLike) {
        const ll = maplibregl.LngLat.convert(lngLatLike);
        marker = new maplibregl.Marker({ draggable: true })
            .setLngLat(ll)
            .addTo(map);
        attachMarkerEvents();
        document.getElementById('clear-marker-btn').parentElement.style.display = 'block';
        updateCircle(ll, radiusKm);
    }

    function setPosition(lngLatLike) {
        if (!marker) return;
        const ll = maplibregl.LngLat.convert(lngLatLike);
        marker.setLngLat(ll);
        updateCircle(ll, radiusKm);
    }

    function wireEvents() {
        onMapClick = e => {
            if (!marker) {
                createMarkerAt(e.lngLat);
            } else {
                marker.setLngLat(e.lngLat);
                updateCircle(e.lngLat, radiusKm);
            }
            callback();
        }
        map.on('click', onMapClick);
    }

    function clearCircle() {
        if (!map) return;
        const src = map.getSource(ids.source);
        if (src) {
            src.setData({ type: 'FeatureCollection', features: [] });
        }
    }

    function removeMarker() {
        if (!map) return;
        if (marker) {
            marker.remove();
            marker = null;
        }
        document.getElementById('clear-marker-btn').parentElement.style.display = 'none';
        clearCircle();
    }


    function init(userMap, {
        startLngLat = null,
        startRadiusKm = 15,
        controlPosition = 'top-left',
        controlOptions = {},
        updateCallback = () => {},
    } = {}) {
        if (!userMap) throw new Error('LocationRadius.init: map is required');
        if (!turf || !turf.circle) throw new Error('LocationRadius.init: turf.circle is required');

        map = userMap;
        radiusKm = startRadiusKm;
        callback = updateCallback;

        const setup = () => {
            setupCircleLayers();
            wireEvents();

            control = new RadiusControl({
                value: startRadiusKm,
                onInput: km => setRadiusKm(km),
                ...controlOptions
            });
            map.addControl(control, controlPosition);

            if (startLngLat !== undefined && startLngLat !== null) {
                createMarkerAt(startLngLat);
            }
        };

        if (!map.isStyleLoaded()) {
            // maybe use map.once('load', setup) ?
            const onLoad = () => { map.off('load', onLoad); setup(); };
            map.on('load', onLoad);
        } else {
            setup();
        }
    }

    function destroy() {
        if (!map) return;

        if (control) {
            map.removeControl(control);
            control = null;
        }

        if (onMapClick) {
            map.off('click', onMapClick);
            onMapClick = null;
        }

        if (marker) {
            marker.remove();
            marker = null;
        }

        [ids.line, ids.fill].forEach(id => {
            if (map.getLayer(id)) map.removeLayer(id);
        });
        if (map.getSource(ids.source)) map.removeSource(ids.source);
        map = null;
    }

    return {
        init, destroy, updateCircle, setRadiusKm, setPosition,
        getRadiusKm: () => radiusKm,
        getMarker: () => marker,
        removeMarker
    }
})();