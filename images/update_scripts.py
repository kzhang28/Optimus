import os
import platform

if platform.system() == "Windows":
	os.system("COPY /Y ..\scripts\init\* cpu\scripts\\")
	os.system("COPY /Y ..\scripts\image-classification\* cpu\scripts\\")
	os.system("COPY /Y ..\scripts\params-distr\* cpu\scripts\\")
	os.system("COPY /Y ..\scripts\cnn-text-classification\* cpu\scripts\\")

	os.system("COPY /Y ..\scripts\init\* gpu\scripts\\")
	os.system("COPY /Y ..\scripts\image-classification\* gpu\scripts\\")
	os.system("COPY /Y ..\scripts\params-distr\* gpu\scripts\\")
	os.system("COPY /Y ..\scripts\cnn-text-classification\* gpu\scripts\\")

elif platform.system() == "Linux":
	os.system("cp ../scripts/init/* cpu/scripts/")
	os.system("cp ../scripts/image-classification/* cpu/scripts/")
	os.system("cp ../scripts/params-distr/* cpu/scripts/")
	os.system("cp ../scripts/cnn-text-classification/* cpu/scripts/")

	os.system("cp ../scripts/init/* gpu/scripts/")
	os.system("cp ../scripts/image-classification/* gpu/scripts/")
	os.system("cp ../scripts/params-distr/* gpu/scripts/")
	os.system("cp ../scripts/cnn-text-classification/* gpu/scripts/")

	# rebuild cpu image
	os.system("cd cpu/ && ./build.sh")