create table users (id varchar(64) primary key);

create table sessions(
    id varchar(64) primary key,
    user_id varchar(64),
    creation timestamp,
    foreign key(user_id) references users(id)
); 

-- test user
insert into users values('c6354001bc5d6538dd856d00aa25a2458e44fd3b9214d4bad2dc06278f6b059f');