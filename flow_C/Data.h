#pragma once
#include<iostream>
#include<fstream>
#include"Table.h"
class Data
{
private:
	float** split;
	
	//void get_density(const char* file,float** table);
public:
	int num_partition;
	int dim;

	Data();
	~Data();
	Data(const char* file_space, int num_partition);
	void save(const char* file);
	void load(const char* file_space);
	void apply_cells(const char* file);
};

