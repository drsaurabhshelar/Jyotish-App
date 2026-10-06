import { isValidDateFormat, isValidTimeFormat } from '../src/utils/validators';

describe('Validators', () => {
  test('isValidDateFormat should validate DD/MM/YYYY dates', () => {
    expect(isValidDateFormat('12/05/1990')).toBe(true);
    expect(isValidDateFormat('31/12/2023')).toBe(true);
    expect(isValidDateFormat('31/02/2023')).toBe(false); // Invalid Feb 31
    expect(isValidDateFormat('1990/05/12')).toBe(false);
    expect(isValidDateFormat('12-05-1990')).toBe(false);
    expect(isValidDateFormat('abc')).toBe(false);
  });

  test('isValidTimeFormat should validate HH:MM AM/PM times', () => {
    expect(isValidTimeFormat('08:35 PM')).toBe(true);
    expect(isValidTimeFormat('8:35 pm')).toBe(true);
    expect(isValidTimeFormat('12:00 AM')).toBe(true);
    expect(isValidTimeFormat('25:00 PM')).toBe(false);
    expect(isValidTimeFormat('08:60 PM')).toBe(false);
    expect(isValidTimeFormat('20:30')).toBe(false);
  });
});
