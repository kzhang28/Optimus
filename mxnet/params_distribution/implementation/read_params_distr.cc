#include <iostream>
#include <fstream>
#include <string>

int main()
{
	std::string line;
	std::ifstream fh;
	fh.open("param_distr.txt");
	while(!fh.eof())
	{
		std::getline(fh, line);
		std::cout << line;
	}
	fh.close();
}
