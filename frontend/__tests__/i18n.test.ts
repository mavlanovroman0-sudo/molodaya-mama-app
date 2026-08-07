import { t, getCurrentLanguage, setLanguage } from '../src/i18n';

describe('i18n', () => {
  it('returns Russian title by default', () => {
    expect(t('app.title')).toBe('HomeEase');
  });

  it('switches language', async () => {
    await setLanguage('kk', false);
    expect(getCurrentLanguage()).toBe('kk');
    expect(t('roles.housewife')).toBe('Үй ханымы');
    await setLanguage('ru', false);
  });

  it('falls back to Russian for missing keys', async () => {
    await setLanguage('uz', false);
    expect(t('app.title')).toBe('HomeEase');
    await setLanguage('ru', false);
  });
});
