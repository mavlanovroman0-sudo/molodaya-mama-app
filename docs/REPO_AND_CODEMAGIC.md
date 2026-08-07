# Репозиторий, GitHub и Codemagic — одна личность, одна папка

Документ фиксирует правила, чтобы **не повторить** прошлый сбой:
проект «не виден» / сборка падает, потому что Git и Codemagic под разными почтами,
а Codemagic запускает команды не в той папке.

## Жёсткие правила

1. **Один email** для трёх мест:
   - вход в GitHub (владелец репозитория);
   - `git config user.email` **в этой папке проекта**;
   - вход в Codemagic (и привязанный к нему GitHub).
2. **Корень git** — только эта папка:
   `c:\Users\USER\moe-delo\app3\молодая мама`  
   Не инициализировать git в `moe-delo`, `app3`, Desktop-копиях.
3. **Мобильное приложение** живёт в подпапке `frontend/`  
   (есть `frontend/package.json` и `frontend/app.json`).  
   В Codemagic: **Project path = `frontend`**.
4. Имя папки сейчас: `молодая мама`.  
   Нигде в CI не использовать старое имя `домохозяйка`.
5. Секреты (`.env`, `.env.production`) в git **не коммитить**.

## Проверка перед первым коммитом

В PowerShell:

```powershell
cd "c:\Users\USER\moe-delo\app3\молодая мама"
.\scripts\verify-repo-identity.ps1
```

Скрипт остановится с ошибкой, если:
- не задан `user.email` / `user.name`;
- текущая папка не корень git;
- нет `frontend/package.json`.

## Как узнать «правильную» почту GitHub

1. Откройте браузер → https://github.com  
2. Войдите в аккаунт, который будет **владельцем** репозитория HomeEase  
   (у этой машины в credential helper указан пользователь `mavlanovroman0-sudo` — используйте именно его, если репозиторий создаёте под ним).  
3. Нажмите аватар (справа сверху) → **Settings**.  
4. Слева: **Emails**.  
5. Скопируйте **Primary email address** (или Verified email, который используете для коммитов).  
6. Эту же почту укажите в Codemagic: https://codemagic.io → войти → тот же GitHub.

## Настройка git (только этот проект)

```powershell
cd "c:\Users\USER\moe-delo\app3\молодая мама"
git config user.email "ТА_ЖЕ_ПОЧТА_ЧТО_В_GITHUB_И_CODEMAGIC"
git config user.name "Ваше Имя"
git config user.email
git config user.name
```

## Codemagic — путь к приложению

| Параметр | Значение |
|----------|----------|
| Репозиторий | тот, что запушен из `молодая мама` |
| Project path | `frontend` |
| Файл workflow | `codemagic.yaml` в корне репозитория |

Каждый скрипт в `codemagic.yaml` сначала проверяет:

```bash
test -f "$CM_BUILD_DIR/frontend/package.json"
cd "$CM_BUILD_DIR/frontend"
```

Так сборка не запустится из корня монорепо «вслепую».

## Контрольный список перед первой сборкой

- [ ] `git config user.email` = Primary email GitHub-аккаунта владельца репо  
- [ ] Codemagic открыт под **тем же** GitHub  
- [ ] В списке приложений Codemagic виден именно HomeEase-репозиторий  
- [ ] На GitHub в репо есть `frontend/package.json` и `frontend/app.json`  
- [ ] Project path = `frontend`  
- [ ] Нет ссылок на папку `домохозяйка`  
