from typing import List

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> List[str]:
    return [
        """CREATE TABLE IF NOT EXISTS "admin" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "password" VARCHAR(200) NOT NULL,
    "last_login" TIMESTAMP NOT NULL  /* Last Login */,
    "email" VARCHAR(200) NOT NULL  DEFAULT '',
    "avatar" VARCHAR(200) NOT NULL  DEFAULT '',
    "intro" TEXT NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "book" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "book_id" INT NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "img_link" VARCHAR(255) NOT NULL,
    "tags" VARCHAR(255) NOT NULL,
    "public_year" INT NOT NULL,
    "description" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "bookauthor" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "author_name" VARCHAR(255) NOT NULL,
    "author_id" INT NOT NULL,
    "book_id" INT NOT NULL REFERENCES "book" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "category" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "slug" VARCHAR(200) NOT NULL,
    "name" VARCHAR(200) NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "config" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "label" VARCHAR(200) NOT NULL,
    "key" VARCHAR(20) NOT NULL UNIQUE /* Unique key for config */,
    "value" JSON NOT NULL,
    "status" SMALLINT NOT NULL  DEFAULT 1 /* on: 1\noff: 0 */
);
CREATE TABLE IF NOT EXISTS "template" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "type" SMALLINT NOT NULL  /* Message: 1\nKey: 2\nSmile: 3 */,
    "title" VARCHAR(100) NOT NULL,
    "body" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""
    ]


async def downgrade(db: BaseDBAsyncClient) -> List[str]:
    return [
        
    ]
