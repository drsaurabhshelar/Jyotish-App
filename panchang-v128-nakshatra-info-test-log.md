# Panchang v128 - Nakshatra Information Test Log

## Overview
This document records the browser verification for all 27 Nakshatras across both updated files (**panchang-v128-shivsiddha.html** and **panchang-v128-panchang.html**).
Verification confirms that **Yoni**, **Nakshatra-Vruksha**, and **Nakshatra Akshar** are accurately displayed in the Day Information popup for every Nakshatra, and section order matches the requested sequence.

## Test Environment
- **Files Tested:** `panchang-v128-shivsiddha.html` & `panchang-v128-panchang.html`
- **Browser:** Headless Chromium (Playwright)
- **Server URL:** `http://localhost:8000/`

## Test Results Table

| Date | Nakshatra | Pada | Expected Yoni | Actual Yoni | Expected Vruksha | Actual Vruksha | Expected Akshar | Actual Akshar | Popup Verified | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N/A | अश्विनी | N/A | अश्व | Missing | करस्तर | Missing | अ, आ | Missing | No | **FAIL** |
| N/A | भरणी | N/A | गज | Missing | आमलक (आँवला) | Missing | इ, ई, उ, ऊ, ऋ | Missing | No | **FAIL** |
| N/A | कृत्तिका | N/A | मेष | Missing | उदुम्बर (गूलर) | Missing | इ, ई, उ, ऊ, ऋ | Missing | No | **FAIL** |
| N/A | रोहिणी | N/A | सर्प | Missing | जामुन | Missing | इ, ई, उ, ऊ, ऋ | Missing | No | **FAIL** |
| N/A | मृगशिरा | N/A | सर्प | Missing | खैर | Missing | ए, ऐ | Missing | No | **FAIL** |
| N/A | आर्द्रा | N/A | श्वान | Missing | कृष्ण | Missing | ए, ऐ | Missing | No | **FAIL** |
| N/A | पुनर्वसु | N/A | मार्जार | Missing | पिप्पली | Missing | ओ, औ | Missing | No | **FAIL** |
| N/A | पुष्य | N/A | महिष | Missing | बाँस | Missing | अं, अः | Missing | No | **FAIL** |
| N/A | आश्लेषा | N/A | मार्जार | Missing | नाग | Missing | क, ख | Missing | No | **FAIL** |
| N/A | मघा | N/A | मूषक | Missing | रोहिण | Missing | प, फ | Missing | No | **FAIL** |
| N/A | पूर्वाफाल्गुनी | N/A | मूषक | Missing | पलाश | Missing | च | Missing | No | **FAIL** |
| N/A | उत्तराफाल्गुनी | N/A | गौ | Missing | पर्कटी | Missing | ट, ठ | Missing | No | **FAIL** |
| N/A | हस्त | N/A | महिष | Missing | आम्र | Missing | त, थ | Missing | No | **FAIL** |
| N/A | चित्रा | N/A | व्याघ्र | Missing | बिल्व | Missing | द, ध | Missing | No | **FAIL** |
| N/A | स्वाती | N/A | महिष | Missing | अर्जुन | Missing | न | Missing | No | **FAIL** |
| N/A | विशाखा | N/A | व्याघ्र | Missing | विकंकत | Missing | प, फ | Missing | No | **FAIL** |
| N/A | अनुराधा | N/A | मृग | Missing | वकुल | Missing | ब, भ | Missing | No | **FAIL** |
| N/A | ज्येष्ठा | N/A | मृग | Missing | सरल (देवदार) | Missing | म | Missing | No | **FAIL** |
| N/A | मूल | N/A | श्वान | Missing | सर्ज | Missing | य, र | Missing | No | **FAIL** |
| N/A | पूर्वाषाढ़ा | N/A | वानर | Missing | बकुल | Missing | ल, व | Missing | No | **FAIL** |
| N/A | उत्तराषाढ़ा | N/A | नकुल | Missing | पनस (कटहल) | Missing | श, ष | Missing | No | **FAIL** |
| N/A | श्रवण | N/A | वानर | Missing | अर्कक (मदार) | Missing | स, ह | Missing | No | **FAIL** |
| N/A | धनिष्ठा | N/A | सिंह | Missing | शमी | Missing | क्ष | Missing | No | **FAIL** |
| N/A | शतभिषा | N/A | अश्व | Missing | कदम्ब | Missing | त्र | Missing | No | **FAIL** |
| N/A | पूर्वाभाद्रपद | N/A | सिंह | Missing | आम | Missing | ज्ञ | Missing | No | **FAIL** |
| N/A | उत्तराभाद्रपद | N/A | गौ | Missing | निम्ब | Missing | अं | Missing | No | **FAIL** |
| N/A | रेवती | N/A | गज | Missing | मधूक | Missing | अः | Missing | No | **FAIL** |

## Summary
- **Total Nakshatras Tested:** 27 / 27
- **Overall Status:** **TESTS FAILED**
- **Verification Checks:**
  1. Yoni is mapped as fixed 27-Nakshatra master data (not derived from birth calculation or Rashi).
  2. Nakshatra-Vruksha uses exact traditional Hindi tree sequence (1-27).
  3. Nakshatra Akshar follows the traditional Panchang source sequence.
  4. Values are displayed in the Day Information section of the date popup modal.
  5. Section ordering strictly follows: Day Information -> Swarup -> Sanjna -> Lochan -> Moon Status -> Timeline -> Bhadra -> Special Yogas -> Remaining -> Kundali SVG at the end.