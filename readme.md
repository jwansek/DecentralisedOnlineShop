# DecentralisedOnlineShop

## About

This is a proof-of-concept for an online shopping system.
My objectives were to make the backend of the system to
show that the idea can work.

Instead of relying on a single server to work, it uses the
bittorrent protocol so that the users can create a 'web',
removing all the intensive parts away from the server.

## Server

The server was made using flask and MySQL. It exports relevent
tables to a SQLite file with the client uses. It also dumps
its images. There is also a small script so the server can act as
the first seeder.

## Client

The client application runs quietly in the tray. The idea is that
it would always be on in the background, downloading and uploading
away. In practice this could also act as a local server, so the user
could shop using a webapp.

## Privacy

In order to address privacy concerns the application uses GPG
for end-to-end encryption and verifying the torrents ultimately
originated from the server.

## Data

`siterip/` was made so that the system has example data and images
to work with. It rips the ASDA website for data.

## Dependencies

The application was built and tested in GNU/Linux. There is no reason
why it shouldn't work in Windows, if you change the config files to the
dependencies' executables.

It needs `7z` and `gpg` executables to work. It also needs `libtorrent`.
No binaries exist of this so you need to [compile the python bindings yourself.](https://www.libtorrent.org/python_binding.html) All other dependencies are in their associated `requirements.txt`