# Panchang v128 - Nakshatra Information Test Log

## Overview
This document records the browser verification for all 27 Nakshatras in **panchang-v128.html**.
Verification confirms that **Yoni**, **Nakshatra-Vruksha**, and **Nakshatra Akshar** are accurately displayed in the Day Information popup for every Nakshatra.

## Test Environment
- **File Tested:** `panchang-v128.html`
- **Browser:** Headless Chromium (Playwright)
- **Server URL:** `http://localhost:8000/panchang-v128.html`

## Test Results Table

| Date | Nakshatra | Pada | Expected Yoni | Actual Yoni | Expected Vruksha | Actual Vruksha | Expected Akshar | Actual Akshar | Popup Verified | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-01-08 | अश्विनी | Pada 3 | अश्व | अश्व | करस्तर | करस्तर | अ, आ | अ, आ | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-09 | भरणी | Pada 3 | गज | गज | आमलक (आँवला) | आमलक (आँवला) | इ, ई, उ, ऊ, ऋ | इ, ई, उ, ऊ, ऋ | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-10 | कृत्तिका | Pada 3 | मेष | मेष | उदुम्बर (गूलर) | उदुम्बर (गूलर) | इ, ई, उ, ऊ, ऋ | इ, ई, उ, ऊ, ऋ | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-11 | रोहिणी | Pada 3 | सर्प | सर्प | जामुन | जामुन | इ, ई, उ, ऊ, ऋ | इ, ई, उ, ऊ, ऋ | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-12 | मृगशिरा | Pada 4 | सर्प | सर्प | खैर | खैर | ए, ऐ | ए, ऐ | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-13 | आर्द्रा | Pada 4 | श्वान | श्वान | कृष्ण | कृष्ण | ए, ऐ | ए, ऐ | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-14 | पुनर्वसु | Pada 4 | मार्जार | मार्जार | पिप्पली | पिप्पली | ओ, औ | ओ, औ | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-15 | पुष्य | Pada 4 | महिष | महिष | बाँस | बाँस | अं, अः | अं, अः | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-16 | आश्लेषा | Pada 4 | मार्जार | मार्जार | नाग | नाग | क, ख | क, ख | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-17 | मघा | Pada 4 | मूषक | मूषक | रोहिण | रोहिण | प, फ | प, फ | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-18 | पूर्वाफाल्गुनी | Pada 3 | मूषक | मूषक | पलाश | पलाश | च | च | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-19 | उत्तराफाल्गुनी | Pada 3 | गौ | गौ | पर्कटी | पर्कटी | ट, ठ | ट, ठ | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-20 | हस्त | Pada 3 | महिष | महिष | आम्र | आम्र | त, थ | त, थ | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-21 | चित्रा | Pada 2 | व्याघ्र | व्याघ्र | बिल्व | बिल्व | द, ध | द, ध | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-22 | स्वाति | Pada 2 | महिष | महिष | अर्जुन | अर्जुन | न | न | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-23 | विशाखा | Pada 1 | व्याघ्र | व्याघ्र | विकंकत | विकंकत | प, फ | प, फ | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-24 | अनुराधा | Pada 1 | मृग | मृग | वकुल | वकुल | ब, भ | ब, भ | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-25 | ज्येष्ठा | Pada 1 | मृग | मृग | सरल (देवदार) | सरल (देवदार) | म | म | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-26 | मूल | Pada 1 | श्वान | श्वान | सर्ज | सर्ज | य, र | य, र | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-28 | पूर्वाषाढ़ा | Pada 4 | वानर | वानर | बकुल | बकुल | ल, व | ल, व | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-01 | उत्तराषाढ़ा | Pada 2 | नकुल | नकुल | पनस (कटहल) | पनस (कटहल) | श, ष | श, ष | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-02 | श्रवण | Pada 2 | वानर | वानर | अर्कक (मदार) | अर्कक (मदार) | स, ह | स, ह | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-03 | धनिष्ठा | Pada 2 | सिंह | सिंह | शमी | शमी | क्ष | क्ष | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-04 | शतभिषा | Pada 2 | अश्व | अश्व | कदम्ब | कदम्ब | त्र | त्र | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-05 | पूर्वाभाद्रपद | Pada 2 | सिंह | सिंह | आम | आम | ज्ञ | ज्ञ | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-06 | उत्तराभाद्रपद | Pada 2 | गौ | गौ | निम्ब | निम्ब | अं | अं | Yes (Verified in Day Information Modal) | **PASS** |
| 2025-01-07 | रेवती | Pada 2 | गज | गज | मधूक | मधूक | अः | अः | Yes (Verified in Day Information Modal) | **PASS** |

## Summary
- **Total Nakshatras Tested:** 27 / 27
- **Overall Status:** **ALL TESTS PASSED**
- **Verification Checks:**
  1. Yoni is mapped as fixed 27-Nakshatra master data (not derived from birth calculation or Rashi).
  2. Nakshatra-Vruksha uses exact traditional Hindi tree sequence (1-27).
  3. Nakshatra Akshar follows the traditional Panchang source sequence.
  4. Values are displayed in the Day Information section of the date popup modal.
  5. Agriculture and Jalashay Khanan sections render at the bottom end of the popup modal.