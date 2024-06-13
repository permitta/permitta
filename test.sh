#! /bin/bash

if [ $1 == 'opa' ]
then
  opa test opa/trino -v
fi