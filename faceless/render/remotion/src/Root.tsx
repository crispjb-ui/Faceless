import React from 'react';
import {Composition} from 'remotion';
import {MotivationVideo, calcMetadata} from './MotivationVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="MotivationVideo"
      component={MotivationVideo}
      durationInFrames={300}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{fps: 30, shots: [], captions: [], voice: '', music: null}}
      calculateMetadata={calcMetadata}
    />
  );
};
