export module hello;
import std;

export void hello(const std::formattable<char> auto& world)
{
    return std::println("hello, {}", world);
}
