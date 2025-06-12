Iako neke HTTPS web-stranice preglednik učitava korektno, python `requests` tj. unutarnji `urllib3` daje SSL error ako dođe do neke miskonfiguracije, no to se može zaobići tako da za `verify=` parametar u requestu damo putanju do datoteke certifikata koji želimo.

Zašto se to događa? Ne znam. Za one koji se žele baviti ovime, evo kako generirati jedan sličan "broken" SSL certifikat:
1. `~/.acme.sh/acme.sh --issue --dns -d moja.domena.com --yes-I-know-dns-manual-mode-enough-go-ahead-please`
2. odradi korake za verifikaciju domene koje acme.sh zahtijeva
3. preimenuj `moja.domena.com.key` u `moja.domena.com.key.pem` ili samo `private.key.pem`
4. `openssl x509 -in moja.domena.com.cer -out domain.cert.pem -outform PEM`
5. pokreni uvicorn server s parametrima `--ssl-keyfile="private.key.pem (file iz #3)" --ssl-certfile="domain.cert.pem"`
6. pošalji `requests.get` na taj server

(pravilan način za pokretanje uvicorn servera sa ssl certifikatima je `--ssl-keyfile="moja.domena.com.key" --ssl-certfile="fullchain.cer"`, datoteke koje generira acme.sh)
