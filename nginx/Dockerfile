FROM nginx:stable-alpine

COPY private.key /etc/ssl/public.key
COPY public.pem /etc/ssl/private.pem

COPY ./default.conf /etc/nginx/conf.d/default.conf