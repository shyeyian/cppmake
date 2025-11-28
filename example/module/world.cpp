export module world;
export import world.better;
export import :ending;
import :secret;
import std;

auto engine = std::mt19937(0); // private
export auto world = std::array{better, ending, secret}[std::uniform_int_distribution(0, 2)(engine)];