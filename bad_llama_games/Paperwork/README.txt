						LLAMA LANDMINE - README
		Clemence Brival, Gregg Wighton, Gordon McColm, Ozgur Onal
		
DESCRIPTION
Llama Landmine is a game created by the team Bad Llama Games. The game takes its primary influence from
Minesweeper but also tasks the user with searching for Llama's as well as avoiding Mines. Registered Users
have their scores posted to the leaderboard, can earn badges, and can send friend requests and challenges 
to other users. 

HOW TO
To install Llama Landmine:

1. Create a new Virtual Environment using "mkvirtualenv --system-site-packages <env_name>",
2. Install the necessary packages using "pip install –U django==1.7.11",
3. Using Git Hub, clone the repository using "git clone https://github.com/gordi1308/LlamaLandmine.git",
4. Move into the LlamaLandmine directory,
5. Move into the badllamagames directory,
6. "python manage.py makemigrations",
7. "python manage.py migrate",
8. "python populate_llamalandmine.py",
9. "python manage.py runserver",
10. Visit "127.0.0.1:8000/llamalandmine/" on your browser
	- For the admin interface visit "127.0.0.1:8000/admin/"
11. To login use Username: leifos, Password: leifos
	- Or use david/david or laura/laura

