create table users (id integer primary key);

create table sessions(
    id integer primary key,
    user_id integer,
    creation date,
    foreign key(user_id) references users(id)
); 
