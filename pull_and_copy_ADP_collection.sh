#! /bin/sh
cd ../ADP_collection/
echo "Pulling changes from ADP_collection git repository."
git pull
echo "Copying .gap and .hh files to the folder ~/bellmanscafe/"
cp ./*.gap ../bellmanscafe/
cp ./*.hh ../bellmanscafe/
echo "Success."
echo "Update was performed at: " >> $HOME/bellmanscafe/gapfiles_updates.log
date >> $HOME/bellmanscafe/gapfiles_updates.log
echo "---------" >> $HOME/bellmanscafe/gapfiles_updates.log
