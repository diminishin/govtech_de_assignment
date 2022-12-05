BEGIN;

-- USERS TABLE REFERS TO INTERNAL COMPANY USERS
CREATE TABLE IF NOT EXISTS users (
	id serial PRIMARY KEY,
	name varchar(255) NOT NULL,
	created_at timestamp,
	modified_at timestamp
);

-- CREATE PRODUCT RELATED TABLES
CREATE TABLE IF NOT EXISTS product_category  (
	id serial PRIMARY KEY,
	name varchar(255) NOT NULL,
	description text,
	created_at timestamp,
	created_by int NOT NULL REFERENCES users,
	modified_at timestamp,
	modified_by int NOT NULL REFERENCES users
);

CREATE TABLE IF NOT EXISTS product_inventory  (
	id serial PRIMARY KEY,
	quantity int NOT NULL,
	created_at timestamp,
	created_by int NOT NULL REFERENCES users,
	modified_at timestamp,
	modified_by int NOT NULL REFERENCES users
);

CREATE TABLE IF NOT EXISTS discount  (
	id serial PRIMARY KEY,
	name varchar(255) NOT NULL,
	description text,
	discount_percent numeric(3,2) NOT NULL,
	active boolean NOT NULL,
	created_at timestamp,
	created_by int NOT NULL REFERENCES users,
	modified_at timestamp,
	modified_by int NOT NULL REFERENCES users
);

CREATE TABLE IF NOT EXISTS product  (
	id serial PRIMARY KEY,
	name varchar(255) NOT NULL,
	description text,
	cost_usd numeric(1000,2),
	weight_kg numeric(1000,2),
	sku varchar(8),
	category_id int NOT NULL REFERENCES product_category,
	inventory_id int NOT NULL REFERENCES product_inventory,
	discount_id int NOT NULL REFERENCES discount,
	created_at timestamp,
	created_by int NOT NULL REFERENCES users,
	modified_at timestamp,
	modified_by int NOT NULL REFERENCES users
);

-- CREATE MEMBER RELATED TABLES

CREATE TABLE IF NOT EXISTS member  (
	id varchar(255) NOT NULL PRIMARY KEY,
	username varchar(255) NOT NULL,
	password varchar(255) NOT NULL,
	first_name varchar(255),
	last_name varchar(255) NOT NULL,
	mobile varchar(8) NOT NULL,
	email varchar(255) NOT NULL,
	birthday varchar(8) NOT NULL,
	created_at timestamp,
	created_by int NOT NULL REFERENCES users,
	modified_at timestamp,
	modified_by int NOT NULL REFERENCES users
);

CREATE TABLE IF NOT EXISTS member_payment  (
	id serial PRIMARY KEY,
	member_id varchar(255) NOT NULL REFERENCES member,
	payment_type varchar(255),
	provider varchar(255),
	account_no varchar(255),
	expiry date,
	created_at timestamp,
	created_by int NOT NULL REFERENCES users,
	modified_at timestamp,
	modified_by int NOT NULL REFERENCES users
);

CREATE TABLE IF NOT EXISTS member_address  (
	id serial PRIMARY KEY,
	member_id varchar(255) NOT NULL REFERENCES member,
	address_line_1 varchar(255),
	address_line_2 varchar(255),
	city varchar(255),
	postal_code varchar(255),
	country varchar(255),
	mobile varchar(8),
	created_at timestamp,
	created_by int NOT NULL REFERENCES users,
	modified_at timestamp,
	modified_by int NOT NULL REFERENCES users
);

-- CREATE ORDER RELATED TABLES

CREATE TABLE IF NOT EXISTS payment_details  (
	id serial PRIMARY KEY,
	order_id int NOT NULL, --This column provides easy reports on payments type without having to join to order_details
	member_id varchar(255) NOT NULL, --This column provides easy reports on payments type without having to join to order_details
	amount numeric(1000,2) NOT NULL,
	provider varchar(255) NOT NULL,
	status varchar(255) NOT NULL,
	created_at timestamp,
	created_by int NOT NULL REFERENCES users,
	modified_at timestamp,
	modified_by int NOT NULL REFERENCES users
);

CREATE TABLE IF NOT EXISTS order_details  (
	id serial PRIMARY KEY,
	member_id varchar(255) NOT NULL REFERENCES member,
	total numeric(1000,2) NOT NULL,
	payment_id int REFERENCES payment_details,
	created_by int NOT NULL REFERENCES users,
	modified_at timestamp,
	modified_by int NOT NULL REFERENCES users
);

CREATE TABLE IF NOT EXISTS order_items  (
	id serial PRIMARY KEY,
	order_id int NOT NULL REFERENCES order_details,
	product_id int NOT NULL REFERENCES product,
	quantity int NOT NULL,
	created_at timestamp,
	created_by int NOT NULL REFERENCES users,
	modified_at timestamp,
	modified_by int NOT NULL REFERENCES users
);

CREATE TABLE IF NOT EXISTS session  (
	id serial PRIMARY KEY,
	member_id varchar(255) NOT NULL REFERENCES member,
	total numeric(1000,2),
	created_at timestamp,
	created_by int NOT NULL REFERENCES users,
	modified_at timestamp,
	modified_by int NOT NULL REFERENCES users
);

CREATE TABLE IF NOT EXISTS cart  (
	id serial PRIMARY KEY,
	member_id varchar(255) NOT NULL REFERENCES member,
	session_id int NOT NULL REFERENCES session,
	product_id int NOT NULL REFERENCES product,
	quantity int NOT NULL,
	created_at timestamp,
	created_by int NOT NULL REFERENCES users,
	modified_at timestamp,
	modified_by int NOT NULL REFERENCES users
);

commit;
