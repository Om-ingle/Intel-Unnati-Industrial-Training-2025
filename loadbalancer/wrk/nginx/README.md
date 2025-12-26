## NGINX


## Installation

```
yum install nginx
```

## Run

```
systemctl start nginx
```

## Config

Update /etc/nginx/nginx.conf with the attached version

## Generate SSL certificate and key for HTTPS connection to work

```
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt 
```

Replace /etc/ssl/private/nginx-selfsigned.key with /path-to-certs-dir/certs/cert.key in conf
Replace /etc/ssl/certs/nginx-selfsigned.crt with /path-to-certs-dir/certs/cert.pem in conf

