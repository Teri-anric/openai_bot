FROM nginx:stable-alpine

COPY private.key /etc/ssl/private.key
COPY public.pem /etc/ssl/public.pem

COPY ./default.conf /etc/nginx/conf.d/default.conf