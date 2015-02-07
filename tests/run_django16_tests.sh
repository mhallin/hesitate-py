#!/bin/sh

set -e

cd tests/django16
$1 manage.py test
