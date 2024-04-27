#!/bin/bash

stock_collector makemigrations
stock_collector migrate
stock_collector runserver 9091
