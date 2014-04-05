# Cosmexoxo

This project is a shopping website supported by a database. The goal is to sell cosmetics, thus the name. But most of the code is reusable for any shopping website.

## Current Status

The database entry software (Product Filler) is ready, and is currently used to fill a database of products.

The website only has navigation bar, and will soon be able to display products taken from the database. From there the cart and payment system needs to be added.

## Running Locally

Asumming you have [Node.js](http://nodejs.org/) and [Heroku Toolbelt](https://toolbelt.heroku.com/) installed on your machine:

```sh
git clone git@github.com:scagnon/cosmexoxo.git # or clone your own fork
cd cosmexoxo
npm install
foreman start
```

Your app should now be running on [localhost:8080](http://localhost:8080/).

## Running the Product Filler

Product Filler is running on Python 2.7, with the following libraries:
* ImageTk: you may have to download the latest version of PIL to make it work.
* [Boto](https://github.com/boto/boto) for AWS connection
* [psycopg2](http://initd.org/psycopg/docs/) for PostgreSQL connection

You will need to create a json file that will represent the key to your database and storage accounts, it should look like this:

```json
{
  "database":{
    "host": "SERVER_LOCATION",
    "database": "DATABASENAME",
    "user": "USERNAME",
    "port": PORT,
    "password": "PASSWORD"
  },
  "aws_access_key":{
  	"aws_access_key_id":"ACCESSKEY",
  	"aws_secret_access_key":"SECRETACCESSKEY"
  },
  "s3_bucket": "BUCKETNAME"
}
```