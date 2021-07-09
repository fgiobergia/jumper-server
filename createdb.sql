create table users (id varchar(64) primary key);

create table sessions(
    id varchar(64) primary key,
    user_id varchar(64),
    creation timestamp,
    closed boolean default false,
    foreign key(user_id) references users(id)
); 