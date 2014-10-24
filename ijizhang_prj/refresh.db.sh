#!/bin/bash
mysql -u root -p<<eof
drop database if exists ijizhang;
CREATE DATABASE ijizhang DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
eof
python ./manage.py syncdb