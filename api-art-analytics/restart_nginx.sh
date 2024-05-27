# restart_nginx

sudo systemctl stop art.service 
sudo systemctl start art.service
sudo systemctl enable art.service

sudo service nginx restart 

sudo chmod -R 777 /home/ec2-user/app