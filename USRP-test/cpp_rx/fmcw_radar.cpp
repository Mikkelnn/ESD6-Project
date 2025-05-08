#include <string>
#include <chrono>
#include "usrp_manager.cpp"

class FMCMRadar {
public:
    FMCMRadar(USRPManager usrp_mgr) : _usrp_mgr(usrp_mgr)
    {

    }

    void startSweep(std::chrono::steady_clock currentTime) {
        for (int beamAngle = startSweepAngleDeg; beamAngle <= endSweepAngleDeg; beamAngle += sweepResolutionDeg) {
            
            var beamBuffer = // ....
            BeamFormer.getBeamAtAngle(defaultChirp, buffer, beamAngle);
            startFrame(beamBuffer);   
        }
    }

    void startFrame(var beamBuffer) {
        for (int i = 0; i < chirpsInFrame; i++) {
            _usrp_mgr.transmit_samples(beamBuffer);
        }
    }
    
private:
    int chirpsInFrame = 128;
    int startSweepAngleDeg = -60;
    int endSweepAngleDeg = 60;
    int sweepResolutionDeg = 5;
    USRPManager _usrp_mgr;
}