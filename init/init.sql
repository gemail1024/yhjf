-- CreateTable
CREATE TABLE "Msg" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "hash" TEXT NOT NULL,
    "type" INTEGER NOT NULL DEFAULT 0,
    "content" TEXT NOT NULL,
    "viewCount" INTEGER NOT NULL DEFAULT 0,
    "destroyType" INTEGER NOT NULL DEFAULT 0,
    "destroyMinutes" INTEGER NOT NULL DEFAULT 0,
    "secret" TEXT,
    "isDeleted" INTEGER NOT NULL DEFAULT 0,
    "passwordAttempts" INTEGER NOT NULL DEFAULT 0,
    "status" INTEGER NOT NULL DEFAULT 0,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME,
    "destroyedAt" DATETIME
);

-- CreateTable
CREATE TABLE "Hash" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "hash" TEXT NOT NULL,
    "used" BOOLEAN NOT NULL DEFAULT false
);

-- CreateIndex
CREATE UNIQUE INDEX "Msg_hash_key" ON "Msg"("hash");

-- CreateIndex
CREATE UNIQUE INDEX "Hash_hash_key" ON "Hash"("hash");
