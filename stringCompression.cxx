#include <cstddef>
#include <string>
#include <cstdlib>
#include <iostream>

std::size_t stringCompression(std::string& str) {
    int n = str.length();
    if (n == 0) return 0;

    int writeIndex = 0;
    int count = 1;
    for (int i = 1; i <= n; ++i) {
        if (i < n && str[i] == str[i - 1]) {
            ++count;
        } else {
            str[writeIndex++] = str[i - 1];
            if (count > 1) {
                std::string countStr = std::to_string(count);
                for (char c : countStr) {
                    str[writeIndex++] = c;
                }
            }
            count = 1;
        }
    }
    str.resize(writeIndex);
    return str.length();
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cout << "Usage: " << std::string(argv[0]) << " <string to compress>" << std::endl;
        return 1; 
    }
    auto out = std::string(argv[1]);
    stringCompression(out);
    std::cout << out << std::endl;
    return 0;
}
