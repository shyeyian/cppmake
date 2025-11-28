module world:secret; // private module partition
import std;

std::string secret = 
    "this is a private module partition and cannot be exported in module `world`" 
    "(but can be visited by other module partition e.g. `world:ending`)";