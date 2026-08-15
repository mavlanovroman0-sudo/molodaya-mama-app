import {
  fireKey,
  formatAlarmTime,
  matchesNow,
  wrapHour,
  wrapMinute,
  type BabyAlarm,
} from '../src/services/babyAlarms';

describe('babyAlarms helpers', () => {
  it('formats time with leading zeros', () => {
    expect(formatAlarmTime(8, 5)).toBe('08:05');
    expect(formatAlarmTime(14, 30)).toBe('14:30');
  });

  it('wraps hours and minutes', () => {
    expect(wrapHour(24)).toBe(0);
    expect(wrapHour(-1)).toBe(23);
    expect(wrapMinute(60)).toBe(0);
    expect(wrapMinute(-1)).toBe(59);
  });

  it('matches enabled alarm at current minute', () => {
    const alarm: BabyAlarm = {
      id: '1',
      kind: 'feeding',
      hour: 9,
      minute: 15,
      enabled: true,
    };
    const now = new Date(2026, 7, 15, 9, 15, 10);
    expect(matchesNow(alarm, now)).toBe(true);
    expect(matchesNow({ ...alarm, enabled: false }, now)).toBe(false);
    expect(matchesNow(alarm, new Date(2026, 7, 15, 9, 16, 0))).toBe(false);
  });

  it('builds a unique fire key per minute', () => {
    const alarm: BabyAlarm = {
      id: 'abc',
      kind: 'sleep',
      hour: 21,
      minute: 0,
      enabled: true,
    };
    const a = fireKey(alarm, new Date(2026, 7, 15, 21, 0, 1));
    const b = fireKey(alarm, new Date(2026, 7, 15, 21, 1, 0));
    expect(a).not.toBe(b);
  });
});
