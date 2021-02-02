# Building
FROM toshikiohnogi/ubuntu-python:ubuntu20.04-python3.9 as build-stage
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
COPY . .
RUN python manager.py build

# Production
FROM nginx:stable-alpine as production-stage
ENV SOURCE_ROOT /usr/share/nginx/html
COPY ./configs/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./configs/robots.txt ${SOURCE_ROOT}
COPY --from=build-stage /app/public ${SOURCE_ROOT}
RUN find ${SOURCE_ROOT}/articles/*/images | grep -e .jpg -e .png | xargs chmod 644
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
