create table bot_user(
    telegram_id bigint not null UNIQUE,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP not null,
    sex varchar(255),
    age int,
    salary int,
    hobbies varchar(255),
    where_live varchar(255)
);

create table cost_category(
    user_id bigint not null,
    cost_sum int not null,
    category_id int not null,
    month int not null,
    foreign key(category_id) references category(id),
    foreign key(user_id) references bot_user(telegram_id)
);


create table category(
    id int not null,
    name varchar(255) not null unique
);


create table product_name(
    user_id bigint not null,
    product_name text not null,
    category_id int not null,
    price int not null,
    created_at timestamp not null, 
    foreign key(category_id) references category(id),
    foreign key(user_id) references bot_user(telegram_id)
);

insert into category(id, name) values
    (10, 'жилье'),
    (20, 'базовая еда'),
    (30, 'лакшери еда'),
    (40, 'спорт'),
    (50, 'транспорт'),
    (60, 'одежда'),
    (70, 'аптека'),
    (80, 'косметика'),
    (90, 'развлечение'),
    (100, 'другое');

    
    