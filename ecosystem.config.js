module.exports = {
  apps: [
    {
      name: "api-brasper",
      script: "gunicorn",
      args: "backend.wsgi:application --bind 0.0.0.0:8808",
      interpreter: "/root/apis-django/Api_BrasPer/venv/bin/python3",
      env: {
        "DJANGO_SETTINGS_MODULE": "backend.settings",
        "PYTHONPATH": "/root/apis-django/Api_BrasPer",
      },
    },
  ],
};
