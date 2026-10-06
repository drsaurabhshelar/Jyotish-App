/**
 * Validates date string in DD/MM/YYYY format
 */
export function isValidDateFormat(dob: string): boolean {
  const regex = /^(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[012])\/(19|20)\d\d$/;
  if (!regex.test(dob.trim())) return false;

  const [day, month, year] = dob.trim().split('/').map(Number);
  const date = new Date(year, month - 1, day);
  return (
    date.getFullYear() === year &&
    date.getMonth() === month - 1 &&
    date.getDate() === day
  );
}

/**
 * Validates time string in HH:MM AM/PM format (e.g. 08:35 PM, 12:00 AM)
 */
export function isValidTimeFormat(time: string): boolean {
  const regex = /^(0?[1-9]|1[0-2]):([0-5][0-9])\s?(AM|PM|am|pm)$/;
  return regex.test(time.trim());
}
