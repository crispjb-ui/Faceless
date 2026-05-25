import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';

type Shot = {img: string; caption: string; durationInFrames: number};

export type MotivationProps = {
  fps: number;
  shots: Shot[];
  voice: string;
  music: string | null;
};

export const calcMetadata = ({props}: {props: MotivationProps}) => {
  const total = props.shots.reduce((a, s) => a + s.durationInFrames, 0) || 1;
  return {durationInFrames: total, fps: props.fps || 30};
};

const KenBurns: React.FC<{src: string; durationInFrames: number}> = ({
  src,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, durationInFrames], [1.05, 1.18], {
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill>
      <Img
        src={staticFile(src)}
        style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`}}
      />
      <AbsoluteFill
        style={{background: 'linear-gradient(transparent 55%, rgba(0,0,0,0.85))'}}
      />
    </AbsoluteFill>
  );
};

const Caption: React.FC<{text: string}> = ({text}) => (
  <AbsoluteFill style={{justifyContent: 'flex-end', padding: '0 70px 320px'}}>
    <p
      style={{
        color: 'white',
        fontFamily: 'Inter, Arial, sans-serif',
        fontWeight: 800,
        fontSize: 76,
        lineHeight: 1.15,
        textAlign: 'center',
        textShadow: '0 4px 24px rgba(0,0,0,0.9)',
        margin: 0,
      }}
    >
      {text}
    </p>
  </AbsoluteFill>
);

export const MotivationVideo: React.FC<MotivationProps> = ({shots, voice, music}) => {
  let from = 0;
  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      {shots.map((shot, i) => {
        const seq = (
          <Sequence key={i} from={from} durationInFrames={shot.durationInFrames}>
            <KenBurns src={shot.img} durationInFrames={shot.durationInFrames} />
            <Caption text={shot.caption} />
          </Sequence>
        );
        from += shot.durationInFrames;
        return seq;
      })}
      {voice ? <Audio src={staticFile(voice)} /> : null}
      {music ? <Audio src={staticFile(music)} volume={0.18} /> : null}
    </AbsoluteFill>
  );
};
