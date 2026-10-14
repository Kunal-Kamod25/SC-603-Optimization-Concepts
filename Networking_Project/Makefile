# Makefile for SC601 Project - Kunal Kamod (MS2513)

CC = gcc
CFLAGS = -Wall
TARGET = net_sim

OBJS = MS2513_main.o MS2513_fun.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS)

MS2513_main.o: MS2513_main.c MS2513_fun.h
	$(CC) $(CFLAGS) -c MS2513_main.c

MS2513_fun.o: MS2513_fun.c MS2513_fun.h MS2513_param.h
	$(CC) $(CFLAGS) -c MS2513_fun.c

clean:
	rm -f $(OBJS) $(TARGET)

run: all
	./$(TARGET)