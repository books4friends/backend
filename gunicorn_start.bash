#!/bin/sh

cd /home/project/vk-books/
exec /home/project/.virtualenvs/vk-books/bin/gunicorn  -c /home/project/vk-books/project/wsgi.py project.wsgi --bind=unix:/home/project/gunicorn.sock