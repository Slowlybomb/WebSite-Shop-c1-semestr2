DROP TABLE IF EXISTS paints;

CREATE TABLE paints
(
    paint_id INTEGER PRIMARY KEY AUTOINCREMENT,
    paint_name TEXT NOT NULL,
    paint_type TEXT,
    paint_description TEXT,
    img_name Text
);

DROP TABLE IF EXISTS paints;

CREATE TABLE paints
(
    paint_id INTEGER PRIMARY KEY AUTOINCREMENT,
    paint_name TEXT NOT NULL,
    paint_type TEXT,
    paint_description TEXT,
    img_name TEXT
);

INSERT INTO paints (paint_name, paint_type, paint_description, img_name)
VALUES
    ('Alleyway Butter Slip, Kilkenny, Paint', 'paint', 'This evocatively named alleyway offers more than just a scenic pathway. Dating back to the early 1600s, Butter Slip gets its unique name from its historic function: it was once the main marketplace for butter trading.', 'alleyway_butter_slip_kilkenny_paint.jpg'),
    ('Phoenix Park, Dublin, Paint', 'paint', 'The biggest park in Ireland. Where live pack of deers', 'phoenix_park_dublin_paint.jpg'),
    ('Enniscorty, Paint', 'paint', 'Enniscorty is the same as Ennis!', 'enniscorty_paint.jpg'),
    ('Skerries, Dublin, Paint', 'paint', 'Skerries is a charming seaside town located in County Dublin, Ireland. Known for its picturesque harbors, sandy beaches, and historic windmills, Skerries is a popular destination for both locals and tourists seeking a blend of natural beauty, heritage, and a vibrant community life.', 'skerries_dublin_paint.jpg'),
    ('Ha''ppenny Bridge, Dublin, Card', 'card', 'The Ha''ppenny Bridge in Dublin.', 'happeny_bridge_dublin_card.jpg'),
    ('Waterford, Card', 'card', 'Waterford is the oldest city in Ireland!', 'waterford_card.jpg'),
    ('Wexford, Card', 'card', 'Wexford is the sunniest county in Ireland!', 'wexford_card.jpg'),
    ('Alleyway Butter Slip, Kilkenny, Card', 'card', 'This evocatively named alleyway offers more than just a scenic pathway. Dating back to the early 1600s, Butter Slip gets its unique name from its historic function: it was once the main marketplace for butter trading.', 'alleyway_butter_slip_kilkenny_card.jpg'),
    ('Forest, Wicklow, Card', 'card', 'The Wicklow Forest in Ireland is renowned for its breathtaking landscapes, featuring lush woodlands, serene lakes, and rugged mountains. It offers a tranquil retreat into nature, providing opportunities for hiking, wildlife observation, and photography.', 'forest_wicklow_card.jpg'),
    ('Ha''ppenny Bridge, Dublin, Print', 'print', 'Are they relatives with Derek Bridge?', 'happeny_bridge_dublin_print.jpg'),
    ('Enniscorty, Print', 'print', 'Enniscorty is the same as Ennis!', 'enniscorty_print.jpg'),
    ('Waterford, Print', 'print', 'Waterford is the oldest city in Ireland!', 'waterford_print.jpg');

DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL
);


DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
);


-- ORDERs
DROP TABLE IF EXISTS orders;


CREATE TABLE orders
(
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    customer_name TEXT,
    customer_surname TEXT,
    customer_email TEXT,
    order_address TEXT,
    comments TEXT,
    order_details TEXT,
    total_price REAL
);
