import { t, getCurrentLanguage, setLanguage } from '../src/i18n';
import { getInstruction } from '../src/i18n/instructionLocales';

describe('i18n', () => {
  it('returns Russian title by default', () => {
    expect(t('app.title')).toBe('молодая мама');
  });

  it('switches language', async () => {
    await setLanguage('kk', false);
    expect(getCurrentLanguage()).toBe('kk');
    expect(t('roles.housewife')).toBe('Үй ханымы');
    await setLanguage('ru', false);
  });

  it('translates title instruction and tariffs', async () => {
    await setLanguage('uz', false);
    expect(t('app.title')).toBe('yosh ona');
    expect(t('common.instruction')).toBe('qoʻllanma');
    expect(t('common.tariffs')).toBe('tariflar');
    await setLanguage('ka', false);
    expect(t('app.title')).toBe('ახალგაზრდა დედა');
    expect(t('common.instruction')).toBe('ინსტრუქცია');
    await setLanguage('ru', false);
  });

  it('falls back to Russian for missing keys', async () => {
    await setLanguage('uz', false);
    expect(t('common.error_generic')).toBe(
      'Не удалось загрузить данные. Проверьте подключение и попробуйте снова.'
    );
    await setLanguage('ru', false);
  });

  it('has change language label in Russian', () => {
    expect(t('common.change_language', 'ru')).toBe('Сменить язык');
  });

  it('has instruction packs for all languages', () => {
    const langs = ['ru', 'kk', 'uz', 'tg', 'ka', 'ky'] as const;
    for (const lang of langs) {
      const pack = getInstruction(lang);
      expect(pack.chapters).toHaveLength(3);
      expect(pack.chapters.map((c) => c.features.length)).toEqual([5, 10, 4]);
      expect(pack.lead.length).toBeGreaterThan(20);
    }
  });
});
