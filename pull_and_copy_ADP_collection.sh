#! /bin/sh
cd ../ADP_collection/
echo "Pulling changes from ADP_collection git repository."
git pull
echo "Copying .gap and .hh files to the directory ~/bellmanscafe/"
cp ./*.gap ../bellmanscafe/
cp ./*.hh ../bellmanscafe/
echo "Success."
echo "Update was performed at: " >> ../bellmanscafe/gapfiles_updates.log
date >> ../bellmanscafe/gapfiles_updates.log
echo "---------" >> ../bellmanscafe/gapfiles_updates.log
echo "gapfiles_updates.log has been updated."
