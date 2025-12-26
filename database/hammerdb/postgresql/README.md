# PostgresQL

## Installation

```
sudo yum update  
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres createuser your_user
sudo -u postgres createdb -O your_user your_database
```

### Fix for missing libgptcl2.1.1.so

```
dnf install libpq
export LD_LIBRARY_PATH=/usr/lib64/
ldd $PATH/workloads/db/HammerDB-4.8/lib/pgtcl2.1.1/libpgtcl2.1.1.so
```

Should return correct linked files

### Fix connection issues

1. /var/lib/pgsql/data/pg_hba.conf
   1. format: type database user address method
   2. type:
      1. local - connection with unix-domain sockets; 
      2. host - connection made using tcp/ip
   3. database - database name; if starts with / then treated as regx
      1. all - matches with all datababes
      2. sameuser - database name is same as username
      3. samerole - requested user must be a memebr of role with same name as the requested database
   4. user - db user; / for regex, + for rolename
      1. all - all users
   5. address - client machine address
      1. CIDR, ipv4, ipv6
      2. all - any ip address
      3. samehost - server ip address
      4. samenet - address on same subnet
   6. auth - authentication method
      1. trust - allow without password
      2. reject - unconditional rejection
      3. md5 - sha-256 or md5 auth  (recomended)
      4. ident - use username of the client by contacting ident sever and chcek if it matches with requested user name
      5. peer - use client os username and match with db user name
      6. cert - for SSL certificate
2. /var/lib/pgsql/data/postgresql.conf 
   1. set listen_address = "*" to allow other than localhost
