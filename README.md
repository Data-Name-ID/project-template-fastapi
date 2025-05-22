# Шаблон проекта на FastAPI

## Создание проекта на основе шаблона

1. Установить `copier`:

    Рекомендуется использовать [uv](https://docs.astral.sh/uv/getting-started/installation)

    ```shell
    uv tool install copier
    ```

2. Создание проекта:

    ```shell
    copier copy --trust . <project_name>
    ```

## TODO

1. Сделать опциональными:
   - авторизацию (+ разные типы авторизации)
   - email
2. Добавить в проект
   - RedisAccessor
   - RabbitMQAccessor
   - AIAgentAccessor
