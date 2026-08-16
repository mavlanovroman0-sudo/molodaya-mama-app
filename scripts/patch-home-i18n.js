const fs = require('fs');
const paths = ['frontend/src/i18n/locales.json', 'i18n/locales.json'];

const titles = {
  ru: 'молодая мама',
  kk: 'жас ана',
  uz: 'yosh ona',
  tg: 'моди ҷавон',
  ka: 'ახალგაზრდა დედა',
  ky: 'жаш эне',
};

const extras = {
  ru: {
    instruction: 'инструкция',
    instruction_title: 'Инструкция',
    tariffs: 'тарифы',
    how_label: 'Как пользоваться',
    result_label: 'Что будет после этого',
    help_label: 'Для чего и чем помогает',
  },
  kk: {
    instruction: 'нұсқаулық',
    instruction_title: 'Нұсқаулық',
    tariffs: 'тарифтер',
    how_label: 'Қалай пайдалану',
    result_label: 'Осыдан кейін не болады',
    help_label: 'Не үшін және қалай көмектеседі',
  },
  uz: {
    instruction: 'qoʻllanma',
    instruction_title: 'Qoʻllanma',
    tariffs: 'tariflar',
    how_label: 'Qanday ishlatish',
    result_label: 'Bundan keyin nima boʻladi',
    help_label: 'Nima uchun va qanday yordam beradi',
  },
  tg: {
    instruction: 'дастур',
    instruction_title: 'Дастур',
    tariffs: 'тарифҳо',
    how_label: 'Чӣ тавр истифода бурдан',
    result_label: 'Баъд аз ин чӣ мешавад',
    help_label: 'Барои чӣ ва чӣ гуна кӯмак мекунад',
  },
  ka: {
    instruction: 'ინსტრუქცია',
    instruction_title: 'ინსტრუქცია',
    tariffs: 'ტარიფები',
    how_label: 'როგორ გამოვიყენოთ',
    result_label: 'რა მოხდება ამის შემდეგ',
    help_label: 'რისთვის და როგორ ეხმარება',
  },
  ky: {
    instruction: 'нускама',
    instruction_title: 'Нускама',
    tariffs: 'тарифтер',
    how_label: 'Кантип колдонуу',
    result_label: 'Андан кийин эмне болот',
    help_label: 'Эмне үчүн жана кантип жардам берет',
  },
};

for (const p of paths) {
  const data = JSON.parse(fs.readFileSync(p, 'utf8'));
  for (const code of Object.keys(titles)) {
    data[code].app.title = titles[code];
    if (data[code].subscription) data[code].subscription.title = titles[code];
    Object.assign(data[code].common, extras[code]);
    for (const key of ['invite_text', 'share_achievement_message', 'share_achievement_prompt']) {
      if (data[code].invite && typeof data[code].invite[key] === 'string') {
        data[code].invite[key] = data[code].invite[key].split('молодая мама').join(titles[code]);
      }
    }
  }
  fs.writeFileSync(p, JSON.stringify(data, null, 2) + '\n');
  console.log('ok', p);
}
