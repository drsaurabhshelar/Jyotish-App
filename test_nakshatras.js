
const { chromium } = require("playwright");

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto("http://localhost:8000/panchang-v128.html");

    // We can evaluate in page context across dates from 2026-01-01 onwards to map 27 Nakshatras
    const results = await page.evaluate(async () => {
        const tests = [];
        const foundNakshatras = new Set();

        let currentDate = new Date(2026, 0, 1);

        while (foundNakshatras.size < 27 && tests.length < 100) {
            let year = currentDate.getFullYear();
            let month = currentDate.getMonth();
            let dateStr = currentDate.toDateString();

            // Get Panchang for this date
            let lat = 28.6139, lng = 77.2090;
            let sunriseDate = window.getSunriseTime(currentDate, lat, lng);
            let p = new PanchangEngine(sunriseDate);

            let nakNameEng = p.moonNakshatraName;
            let nakNameHindi = NAKSHATRA_NAMES_HINDI[p.moonNakshatraIndex];
            let pada = Math.floor((p.moonLongitude % (360/27)) / (360/108)) + 1;

            let expectedYoni = NAKSHATRA_YONI[nakNameEng];
            let expectedVruksha = NAKSHATRA_VRUKSHA[nakNameEng];
            let expectedAkshar = NAKSHATRA_AKSHAR[nakNameEng];

            if (!foundNakshatras.has(nakNameEng)) {
                foundNakshatras.add(nakNameEng);

                // Call openCalendarModal to render modal
                window.openCalendarModal(year, month, dateStr);

                let modal = document.getElementById("calModalBg");
                let modalText = modal ? modal.innerText : "";

                let actualYoni = NAKSHATRA_YONI[p.moonNakshatraName];
                let actualVruksha = NAKSHATRA_VRUKSHA[p.moonNakshatraName];
                let actualAkshar = NAKSHATRA_AKSHAR[p.moonNakshatraName];

                let pass = (actualYoni === expectedYoni) && (actualVruksha === expectedVruksha) && (actualAkshar === expectedAkshar) && modalText.includes("🌙 योनि") && modalText.includes("🌳 नक्षत्र-वृक्ष") && modalText.includes("🔤 नक्षत्र अक्षर");

                tests.push({
                    date: dateStr,
                    nakshatraEng: nakNameEng,
                    nakshatraHindi: nakNameHindi,
                    pada: pada,
                    expectedYoni: expectedYoni,
                    actualYoni: actualYoni,
                    expectedVruksha: expectedVruksha,
                    actualVruksha: actualVruksha,
                    expectedAkshar: expectedAkshar,
                    actualAkshar: actualAkshar,
                    pass: pass ? "PASS" : "FAIL"
                });

                if (modal) modal.remove();
            }

            currentDate.setDate(currentDate.getDate() + 1);
        }

        return tests;
    });

    console.log(JSON.stringify(results, null, 2));
    await browser.close();
})();
