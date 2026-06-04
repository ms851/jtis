import { describe, it, expect } from 'vitest';
import i18n from './i18n';

describe('i18n', () => {
  it('has a valid language configured', () => {
    // fallbackLng is 'de', but LanguageDetector may pick up navigator language
    expect(i18n.options.fallbackLng).toContain('de');
  });

  it('translates app title', () => {
    expect(i18n.t('app.title')).toBe('JTIS');
  });

  it('switches to English', async () => {
    await i18n.changeLanguage('en');
    expect(i18n.t('nav.events')).toBe('Events');
    await i18n.changeLanguage('de');
    expect(i18n.t('nav.events')).toBe('Veranstaltungen');
  });
});
