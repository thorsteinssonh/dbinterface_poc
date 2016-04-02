FROM ubuntu:14.04
MAINTAINER thorsteinssonh@gmail.com

# Run OS preparation
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y aptitude
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y htop
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python python-dev
RUN apt-get clean

# Run install Apache2 services
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y apache2 libapache2-mod-wsgi libapache2-mod-proxy-html
RUN apt-get clean

# Run Configure Apache2
RUN ln -s /etc/apache2/mods-available/proxy_http.load    /etc/apache2/mods-enabled/proxy_http.load
RUN a2enmod ssl && a2enmod proxy && a2enmod proxy_http && a2enmod headers && a2enmod expires && a2enmod wsgi && a2enmod rewrite
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf && rm /var/www/html/index.html /etc/apache2/sites-enabled/*
COPY default.conf /etc/apache2/sites-available/

RUN mkdir /etc/apache2/ssl && \
   openssl genrsa 1024 > /etc/apache2/ssl/self_signed.key && \
   chmod 400 /etc/apache2/ssl/self_signed.key && \
   openssl req -new -x509 -nodes -sha1 -days 365 \ 
       -subj "/C=TW/ST=Denial/L=Taipei/O=Dis/CN=localhost" \
       -key /etc/apache2/ssl/self_signed.key > /etc/apache2/ssl/self_signed.cert && \
   openssl x509 -noout -fingerprint -text < /etc/apache2/ssl/self_signed.cert > /etc/apache2/ssl/self_signed.info
   
RUN a2ensite default

# Application
ADD web2py /var/www/html/
RUN mv /var/www/html/handlers/wsgihandler.py /var/www/html/wsgihandler.py
RUN chown -R www-data:www-data /var/www/html/

# Insert main job script
COPY apache2-foreground /usr/local/bin/

# Expose ports
EXPOSE 80 443

# CMD
CMD apache2-foreground

