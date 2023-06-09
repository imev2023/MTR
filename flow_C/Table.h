#pragma once
#include<iostream>
#include<fstream>
#include <math.h>

class Table
{
protected:
	int binary_search(float value, int pos_i, int pos_f, int dim);
	void readFile(const char* file, int& n_lin, int& n_col, int& y, float*& dados);
	float** table;
public:
	int dim;
	int num_partition;
	int num_channel;
	float** split;

	virtual void get_density(const char* file) = 0;
	virtual void get_density(const char* file, float*& dados) = 0;
	virtual void log_transform()=0;
	//	virtual void standart();
	//	virtual void cell_file(const char* file);
};

class Table1D : private Table {
public:
	Table1D(int num_partition,int num_channel,float** split);
	~Table1D();
	void get_density(const char* file);
	void get_density(const char* file, float*& dados);
	void log_transform();

};

class Table2D : private Table {
public:
	Table2D(int num_partition, int num_channel,float** split);
	~Table2D();
	void get_density(const char* file);
	void get_density(const char* file, float*& dados);
	void log_transform();
};

class Table3D : private Table {	
public:
	Table3D(int num_partition, int num_channel, float** split);
	~Table3D();
	void get_density(const char* file);
	void get_density(const char* file, float*& dados);
	void log_transform();
};

