create table entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null,
  time datetime not null
);	
create table users (
 userid integer primary key autoincrement,
username text not null,
password text not null);